# Two Kinds Comic Web Scraper
Not sure what to say, does exactly what it says on the tin.

It reaches out to [Two Kinds Keenspot's website](https://twokinds.keenspot.com) then fetches the HTML code and extracts any `<img>` tags and then looks for the site's CDN that hosts the comics it self and finally downloads.

Configurable and (in my opinion and testing) foolproof. :p
###### But you can prove me wrong >:p

## Usage
All you need is python installed than you run the `app.py`.

Example: `$ python app.py --start 0 --end 10`

## Options
* `--start` Starting range
* `--end` Ending range
* `--path` Download directory, defaults to `./download`
* `--wait` How long to wait (in seconds) after each batch (of downloads). 0 to disable.
* `--limit` The limit of downloads per batch. 0 to disable.

###### Note that if either `wait` or `limit` is set to 0, the other is not applicable and therefore is disabled.

## Feedback is welcomed!
This is first (public) project for me, so any constructive feedback is appreciate. :3