// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "@chainlink/contracts/src/v0.6/VRFConsumerBase.sol";

import "@openzeppelin/contracts/access/Ownable.sol";

contract Lottery is VRFConsumerBase, Ownable {

    address payable[] public players;
    uint256 public usdEntryFee;
    address public recentWinner;
    uint256 public randomness;
    AggregatorV3Interface internal ethUsdPriceFeed; // For converting usd to eth
    enum LOTTERY_STATE {
        OPEN,
        CLOSED,
        CALCULATING_WINNER
    }
    LOTTERY_STATE public lotteryState;
    uint256 public fee;
    bytes32 public keyHash; // Identifies uniquely the Chainlink VRF node
    
    event RequestedRandomness(bytes32 requestId); // We do it for tracking 
// The random number and then using for testing, since emit uses much less gas
// than saving the variable in storage, cause both are saved in the blockchain
// but the event are not accesible by smart contracts.
// And it'll be difficult to get the return type of the function.

    constructor(address _priceFeedAddress, 
                address _vrfCoordinator,
                 address _link,
                 uint256 _fee,
                 bytes32 _keyHash) 
        public VRFConsumerBase(_vrfCoordinator, _link) {
        usdEntryFee = 50 * (10**18);
        ethUsdPriceFeed = AggregatorV3Interface(_priceFeedAddress);
        lotteryState = LOTTERY_STATE.CLOSED; // or 1
        fee = _fee;
        keyHash = _keyHash;
    }

    function enter() public payable {
        require(lotteryState == LOTTERY_STATE.OPEN, "Is not open yet");
        // $50 minimum
        require(msg.value >= getEntranceFee(), "Not enough ETH");
        players.push(payable(msg.sender));
    }

    function getEntranceFee() public view returns (uint256) {

// We have to pass the commas of the n° of parameters to set them as None,
// But otherwise it won't compile
        (, int price, , , ) = ethUsdPriceFeed.latestRoundData();
// We want a 18 decimals number for working with usd and eth. Seems an arbitrary number
// (Because Solidity hasn't got decimals)

// The eth price from aggregator has 8 decimals so we multiply this for 10**10 to get 18 decimals
        uint256 adjustedPrice = uint256(price) * 10**10; 

        uint256 costToEnter = (usdEntryFee * 10**18) / adjustedPrice; // 18 decimals for usd too

        return costToEnter;
    }

    function startLottery() public onlyOwner {
        require(lotteryState == LOTTERY_STATE.CLOSED,
         "Lottery is already open");
         lotteryState = LOTTERY_STATE.OPEN;
    }

    function endLottery() public onlyOwner {
        require(lotteryState == LOTTERY_STATE.OPEN,
         "Lottery is already closed");
         lotteryState = LOTTERY_STATE.CALCULATING_WINNER;
         bytes32 requestId = requestRandomness(keyHash, fee);
         emit RequestedRandomness(requestId);
    }

    function fulfillRandomness(bytes32 _requestId, uint256 _randomness) internal override {
        require(lotteryState == LOTTERY_STATE.CALCULATING_WINNER,
         "Lottery is not calculating the winner");
        require(_randomness > 0, "Random not found");
        uint256 IndexOfWinner = _randomness % players.length; // For getting a value that's in the list idx
        recentWinner = players[IndexOfWinner];
        payable(recentWinner).transfer(address(this).balance);

        // Reset the lottery
        players = new address payable[](0);
        lotteryState = LOTTERY_STATE.CLOSED;
        randomness = _randomness;
    }

}