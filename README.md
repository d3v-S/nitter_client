# nitter_client

## What is this?
A client for nitter ( Please see https://github.com/zedeus/nitter, thanks to zedeus ), written in PyQt5.

## Requirements
Mostly things in requirements.txt. (should not really work with pip as of now.)

## Installation and run:
Nothing fancy as of now.
Download and run:
``` python3 nitter_client.py ```

## Working:
### username/hashtag
write a hashtag or username (both without @ and #) in input field and click submit.
It may take sometime to load it, you can see "downloading" written near the input field.
Clicking on username will open the username related stuff in next tab.

### auto refresh interval 
there is a spinbox at the end of first row, which sets the update interval in minutes.
New messages are added at the end.

## File Description:
### nitter_parser
- generic code to parse specific items out of rss feed of nitter. Can be used for any feed, just give it a key_list to parse.
- It has a list of nitter instances, which it cycles through in case of failure from domain to another.

### nitter_client
- gui specific stuff.


## Issues and future features:
- uses scrollarea, should be memory heavy.
- does not store which hastags/users follow.
- No notification on new messages
- currently, 0 optimisation and shitty code, but works.
- packaging it properly.
