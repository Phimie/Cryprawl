# Changelog

## [Unreleased]

- 

## [0.0.4-alpha.1] - 2025-08-11

**This is an Alpha test build!**

### Changed

- Renamed the game to Cryprawl  
- Replaced the game icon  

### Added

- Set key binding  
- Exit key binding  
- Settings screen  
- Main title screen  
- Full-screen toggle (windowed / full-screen)

### Improved

- Introduced state constants and refactored all sprites and the main process state machine  
- Enhanced code structure and readability  

## [0.0.3] - 2025-08-10

### Changed

- Repositioned bullet counter display  
- Increased starting health  
- Increased starting bullet count  
- Replaced enemy hit sprite  

### Added

- New enemy Batmage: spawns outside boundaries and periodically summons Bats  
- New enemy Bat: tracks the player  
- 1-second invulnerability after taking damage  
- Scoring and extra-bullet logic for defeating Batmage and Bat  
- Full sprite animation sets for Batmage and Bat  
- Behavior logic for Batmage and Bat  

### Improved

- Added acceleration system; knock-back effects fully optimized  

## [0.0.2] - 2025-08-09

### Fixed

- Bullets no longer remain after game over  

### Changed

- Replaced score textures  
- Replaced enemy hit and death animations  
- Replaced background textures  
- Replaced bullet textures  
- Adjusted window size  
- Adjusted playable area  
- Enemies leaving the bottom edge no longer deduct points  
- Updated enemy movement boundaries  
- UI is now hidden on game over  

### Added

- Audio: BGM, game-over, hit, shoot…  
- Mouse-controlled bullet direction  
- Player health and health UI  
- Player collision deals 100 damage to enemies and reduces player health  
- Player death animation  
- Score penalty on taking damage  

## [0.0.1] - 2025-08-08

### Changed

- Replaced enemy sprite  

### Added

- Bullet counter UI and bullet damage  
- Enemy death animation and enemy health  
- Background  

### Improved

- Reduced memory usage when loading background images  
- Switched keyboard handling to `pygame.key.get_pressed()` for faster response  

## [0.0.0] - 2025-08-07

### Added

- Initial release: controllable character, basic shooting, enemy spawning, scoring system