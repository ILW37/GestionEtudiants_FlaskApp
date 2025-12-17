// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract DiplomaNFT is ERC721, ERC721URIStorage, Ownable {
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIdCounter;
    
    struct DiplomaInfo {
        string studentName;
        string degreeType;
        string institution;
        uint256 issueDate;
        bool isValid;
    }
    
    mapping(uint256 => DiplomaInfo) public diplomas;
    
    event DiplomaMinted(uint256 indexed tokenId, address indexed student, string studentName);
    event DiplomaRevoked(uint256 indexed tokenId);
    
    constructor() ERC721("DiplomaToken", "DIPLOMA") Ownable(msg.sender) {}
    
    function mintDiploma(
        address studentAddress,
        string memory tokenURI,
        string memory studentName,
        string memory degreeType,
        string memory institution
    ) public onlyOwner returns (uint256) {
        require(studentAddress != address(0), "Adresse invalide");
        require(bytes(tokenURI).length > 0, "URI vide");
        
        uint256 tokenId = _tokenIdCounter.current();
        _tokenIdCounter.increment();
        
        _safeMint(studentAddress, tokenId);
        _setTokenURI(tokenId, tokenURI);
        
        diplomas[tokenId] = DiplomaInfo({
            studentName: studentName,
            degreeType: degreeType,
            institution: institution,
            issueDate: block.timestamp,
            isValid: true
        });
        
        emit DiplomaMinted(tokenId, studentAddress, studentName);
        
        return tokenId;
    }
    
    function revokeDiploma(uint256 tokenId) public onlyOwner {
        require(_ownerOf(tokenId) != address(0), "Token inexistant");
        diplomas[tokenId].isValid = false;
        emit DiplomaRevoked(tokenId);
    }
    
    function isDiplomaValid(uint256 tokenId) public view returns (bool) {
        require(_ownerOf(tokenId) != address(0), "Token inexistant");
        return diplomas[tokenId].isValid;
    }
    
    function getDiplomaInfo(uint256 tokenId) public view returns (
        string memory studentName,
        string memory degreeType,
        string memory institution,
        uint256 issueDate,
        bool isValid
    ) {
        require(_ownerOf(tokenId) != address(0), "Token inexistant");
        DiplomaInfo memory info = diplomas[tokenId];
        return (info.studentName, info.degreeType, info.institution, info.issueDate, info.isValid);
    }
    
    function totalSupply() public view returns (uint256) {
        return _tokenIdCounter.current();
    }
    
    function tokenURI(uint256 tokenId) public view override(ERC721, ERC721URIStorage) returns (string memory) {
        return super.tokenURI(tokenId);
    }
    
    function supportsInterface(bytes4 interfaceId) public view override(ERC721, ERC721URIStorage) returns (bool) {
        return super.supportsInterface(interfaceId);
    }
    
    function _update(address to, uint256 tokenId, address auth) internal override(ERC721) returns (address) {
        return super._update(to, tokenId, auth);
    }
}
