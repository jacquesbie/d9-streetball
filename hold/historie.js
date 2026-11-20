// Famous teams for the team maker (20 Nov 2026, user: "Hold generatoren skal også lave en sammenligning af hvem holdet
// er historisk. Så i 3v3 skal den finde en trio og så fremdeles"). Two lists:
//   spillere: key | Full name=short | traits on NBA_F (the scouting report's 23 traits) against an average NBA player,
//             -2.5..+2.5, the same scale as the NBA list and the famous duos in the stats page (../index.html)
//   hold:     team and year | one line about it | the players' keys. The number of keys is the team size: a team of three
//             is compared with the trios, four with the quartets, five with the fives. Teams of two use the stats page's
//             own list of famous duos (DUOS), so the two pages name the same pairs.
// index.html (this folder) does the matching: every way of handing the roles out is tried and the best one counts.
window.D9_HIST = {
  spillere: `
MJ|Michael Jordan=Jordan|usg 2.5 pts 2.5 midFG 1.5 pullup 1.5 clutch 2 stl 1.5 impact 2 win 2 assisted -1
Pippen|Scottie Pippen=Pippen|ast 1.5 stl 2 reb 1 blk 0.5 impact 1.5 win 2 motor 1 drive 1
Rodman|Dennis Rodman=Rodman|reb 2.5 oreb 2.5 usg -2.5 pts -2 putback 1 motor 2 stl 0.5 win 2 sast 1
Harper|Ron Harper=Harper|stl 1 usg -1.5 pts -1 win 2 tov -0.5 longShare -0.5
Longley|Luc Longley=Longley|sast 1.5 reb 0.5 blk 1 usg -1 pts -1 longShare -2.5 win 2 motor -1
Kukoc|Toni Kukoč=Kukoč|ast 1 longShare 1 catch 1 usg 0.5 win 2 clutch 1
Curry|Stephen Curry=Curry|longShare 2 longFG 2 eff 1.5 pts 1.5 usg 1 motor 1.5 ast 1 impact 1.5 win 2
Klay|Klay Thompson=Klay|longShare 2 longFG 1.5 catch 2 assisted 2 ast -1 pts 1 stl 0.5 win 2
KD|Kevin Durant=Durant|pts 2.5 eff 2 pullup 1.5 midFG 1.5 longFG 1 usg 1.5 blk 0.5 win 1.5
Draymond|Draymond Green=Draymond|ast 2 sast 2.5 stl 1.5 blk 1 reb 1.5 usg -2 pts -1.5 eff -0.5 win 2
Iguodala|Andre Iguodala=Iguodala|stl 1.5 ast 1 usg -1.5 pts -1 win 2 impact 1 tov -1 drive 0.5
Barnes|Harrison Barnes=Barnes|catch 1.5 assisted 1.5 usg -0.5 ast -1 win 1.5 longShare 0.5
LeBron|LeBron James=LeBron|drive 2 rimFG 1.5 ast 2 pts 2 reb 1 impact 2.5 win 1.5 usg 1.5 blk 0.5
Wade|Dwyane Wade=Wade|drive 2 stl 1.5 blk 1 pts 1.5 longShare -1.5 usg 1.5 win 1.5 midFG 0.5
Bosh|Chris Bosh=Bosh|midFG 1.5 catch 1 assisted 1.5 reb 1 blk 0.5 usg -0.5 win 1.5 ast -1
RayAllen|Ray Allen=Ray Allen|longShare 2 longFG 2 catch 1.5 assisted 1.5 motor 1.5 clutch 1.5 ast -0.5 reb -1
Chalmers|Mario Chalmers=Chalmers|stl 1 longShare 1 tov 1 usg -1 pts -1 win 1.5
Pierce|Paul Pierce=Pierce|pts 1.5 clutch 2 pullup 1.5 usg 1.5 drive 1 win 2 midFG 1
KG|Kevin Garnett=Garnett|reb 2 blk 1.5 stl 1 midFG 1.5 impact 2 sast 1.5 win 2 motor 1.5
Rondo|Rajon Rondo=Rondo|ast 2.5 stl 2 reb 1 longShare -2 longFG -1.5 usg -1 tov 1 win 1.5
Perkins|Kendrick Perkins=Perkins|sast 2 reb 1 blk 1 usg -2 pts -2 tov 1 longShare -2.5 win 1.5 motor -1
Duncan|Tim Duncan=Duncan|reb 2 blk 2 midFG 1 impact 2 win 2 tov -0.5 longShare -2 sast 1 pts 1
Parker|Tony Parker=Parker|drive 2 rimFG 1 ast 1 pts 1 longShare -1.5 win 2 motor 1 midFG 0.5
Manu|Manu Ginóbili=Ginóbili|drive 1.5 stl 1.5 ast 1 tov 1 longShare 1 clutch 1.5 motor 1.5 usg 0.5 win 2
Kawhi14|Kawhi Leonard=Kawhi|stl 2 eff 1 catch 1 usg -0.5 reb 1 win 2 impact 1.5 tov -1
Kawhi19|Kawhi Leonard=Kawhi|pts 2 midFG 2 stl 1.5 eff 1.5 clutch 2 usg 1.5 impact 2
DGreen|Danny Green=Danny Green|longShare 2 catch 2 assisted 2 stl 0.5 blk 0.5 usg -1.5 ast -1.5 win 1.5
Bird|Larry Bird=Bird|pts 2 longFG 1.5 ast 1.5 reb 1.5 clutch 2 impact 2 win 2
McHale|Kevin McHale=McHale|rimFG 2 eff 2 blk 1.5 reb 1 ast -1.5 longShare -2.5 win 2 pts 1
Parish|Robert Parish=Parish|reb 2 blk 1 midFG 1 sast 1 usg -0.5 longShare -2.5 win 2
DJ|Dennis Johnson=Dennis Johnson|stl 1.5 ast 1 clutch 1.5 midFG 0.5 usg -0.5 win 2 tov -0.5
Ainge|Danny Ainge=Ainge|longShare 1.5 longFG 1 stl 1 motor 1 usg -0.5 win 2
Magic|Magic Johnson=Magic|ast 2.5 reb 1 tov 1 impact 2 win 2 longShare -1 pts 1
Kareem|Kareem Abdul-Jabbar=Kareem|pts 1.5 rimFG 1.5 midFG 1 assisted 1.5 blk 1.5 reb 1 longShare -2.5 win 2
Worthy|James Worthy=Worthy|drive 1.5 rimFG 2 assisted 1.5 motor 2 pts 1 clutch 1.5 longShare -2 win 2
Scott|Byron Scott=Byron Scott|longShare 1 longFG 1 catch 1.5 assisted 1.5 stl 0.5 ast -1 win 2
ACGreen|A.C. Green=A.C. Green|reb 1.5 oreb 1.5 putback 1 usg -1.5 motor 1.5 win 2 ast -1.5
Kyrie|Kyrie Irving=Kyrie|pullup 2 usg 1.5 pts 1.5 clutch 2 assisted -2 reb -1.5 drive 1.5
Love|Kevin Love=Love|reb 2 longShare 1.5 catch 1.5 assisted 1 ast 0.5 blk -1 stl -1 motor -1
TT|Tristan Thompson=Tristan Thompson|oreb 2.5 reb 1.5 putback 2 usg -2 pts -1.5 longShare -2.5 sast 1 ast -1.5
JRSmith|J.R. Smith=J.R. Smith|longShare 2 catch 1 pullup 1 eff -0.5 ast -1 usg 0.5 stl 0.5
Westbrook|Russell Westbrook=Westbrook|usg 2 drive 2 ast 1.5 tov 2 reb 1 motor 2 eff -1 stl 1
Harden12|James Harden=Harden|drive 1.5 eff 1.5 ast 1 longShare 1 usg 0.5 tov 1 assisted -1
Harden18|James Harden=Harden|usg 2.5 pts 2.5 longShare 2 assisted -2.5 tov 1.5 ast 1.5
Ibaka|Serge Ibaka=Ibaka|blk 2.5 reb 1 midFG 1 assisted 1.5 usg -1 ast -2
Shaq|Shaquille O'Neal=Shaq|rimFG 2 reb 2 oreb 1.5 blk 1.5 pts 2 usg 1.5 longShare -2.5 putback 1.5 impact 2 win 1.5
Kobe|Kobe Bryant=Kobe|usg 2 pts 2 pullup 2 midFG 1 clutch 1.5 assisted -1.5 stl 1 win 1.5
Fisher|Derek Fisher=Fisher|longShare 1 catch 1 clutch 1.5 usg -1.5 pts -1 tov -0.5 win 1.5 stl 0.5
Horry|Robert Horry=Horry|clutch 2.5 longShare 1 catch 1.5 blk 1 usg -1.5 pts -1 win 2 reb 0.5
Fox|Rick Fox=Rick Fox|stl 0.5 longShare 0.5 usg -1 win 1.5 ast 0.5
Isiah|Isiah Thomas=Isiah|ast 2 usg 1.5 stl 1.5 tov 1.5 clutch 1.5 drive 1
Dumars|Joe Dumars=Dumars|stl 1 midFG 1 tov -1 usg -0.5 eff 0.5 win 1.5 pullup 1
Laimbeer|Bill Laimbeer=Laimbeer|reb 2 longShare 1 catch 1 sast 1.5 motor -1.5 blk 0.5 drive -1.5 win 1.5
Aguirre|Mark Aguirre=Aguirre|pts 1 midFG 1 usg 1 ast -0.5 win 1.5
Hakeem|Hakeem Olajuwon=Hakeem|blk 2 reb 2 stl 1.5 midFG 1.5 pts 2 usg 2 longShare -2
Drexler|Clyde Drexler=Drexler|drive 1.5 reb 1 ast 1 stl 1 pts 1 motor 1
KSmith|Kenny Smith=Kenny Smith|longShare 1.5 longFG 1.5 catch 1 ast 0.5 reb -1.5 usg -0.5
Cassell|Sam Cassell=Cassell|clutch 2 pullup 1.5 midFG 1 ast 1 usg 0.5 reb -1
Nash|Steve Nash=Nash|ast 2.5 eff 2 longFG 1.5 tov 0.5 usg -0.5 reb -1.5 blk -1 motor 1
Amare|Amar'e Stoudemire=Amar'e|rimFG 2 pts 2 assisted 2 drive 1 reb 1 usg 1.5 longShare -2
Marion|Shawn Marion=Marion|reb 1.5 stl 1.5 blk 1 motor 2 assisted 1.5 putback 1 ast -1 catch 1
JJ|Joe Johnson=Joe Johnson|longFG 1.5 catch 1 pullup 1 pts 0.5 ast 0.5 clutch 1
QRich|Quentin Richardson=Q-Rich|longShare 2.5 catch 1.5 reb 0.5 eff -0.5 ast -1 drive -1
Jokic|Nikola Jokić=Jokić|ast 2 reb 2 eff 2 impact 2.5 rimFG 1.5 pts 1.5 motor -1
Murray|Jamal Murray=Murray|pullup 1.5 longFG 1 clutch 2 assisted 1 pts 1 usg 1
Gordon|Aaron Gordon=Aaron Gordon|rimFG 2 assisted 2 putback 1.5 drive 1 sast 1 longShare -1.5 usg -1 blk 0.5
MPJ|Michael Porter Jr.=Porter Jr.|assisted 2 longShare 1.5 longFG 1.5 catch 1.5 reb 0.5 ast -1.5 stl -1
KCP|Kentavious Caldwell-Pope=Caldwell-Pope|stl 1 catch 1.5 longFG 1 usg -1.5 pts -1 ast -1 win 1
Giannis|Giannis Antetokounmpo=Giannis|drive 2.5 rimFG 2 reb 2 blk 1 pts 2 usg 2 longFG -1.5 longShare -1.5 impact 2
Middleton|Khris Middleton=Middleton|midFG 1.5 pullup 1.5 longFG 1 clutch 1.5 catch 1
Holiday|Jrue Holiday=Holiday|stl 1.5 impact 1.5 win 2 tov -1 midFG 1 ast 1 eff 0.5 usg -0.5 clutch 1
Lopez|Brook Lopez=Brook Lopez|blk 2.5 longShare 1.5 catch 1.5 reb 0.5 motor -1.5 ast -1.5 sast 1
Tucker|P.J. Tucker=Tucker|stl 1 catch 1.5 usg -2 pts -2 oreb 1 sast 1 win 1.5 longShare 1
Tatum|Jayson Tatum=Tatum|pts 1.5 usg 1.5 longShare 1.5 reb 1.5 ast 1 pullup 1 win 2
Brown|Jaylen Brown=Jaylen Brown|pts 1.5 usg 1.5 drive 1.5 stl 1 tov 1 win 2 midFG 0.5
White|Derrick White=Derrick White|eff 1.5 tov -1.5 win 2 impact 1.5 usg -1 blk 1 stl 0.5 clutch 1 longShare 1 motor 1
Porzingis|Kristaps Porziņģis=Porziņģis|blk 2 longShare 1 eff 1.5 catch 1 reb 0.5 ast -1.5 motor -0.5 win 1.5
Dirk|Dirk Nowitzki=Dirk|midFG 2.5 pullup 2 pts 2 clutch 2 reb 1 usg 1.5 drive -1
Terry|Jason Terry=Terry|longShare 1.5 longFG 1.5 clutch 1.5 catch 1 reb -1.5 usg 0.5
Kidd|Jason Kidd=Kidd|ast 2 stl 1 longShare 1 usg -1.5 pts -1.5 reb 1 win 1.5 tov 0.5
Chandler|Tyson Chandler=Chandler|rimFG 2 reb 2 oreb 1.5 blk 1.5 sast 1.5 usg -2 assisted 2 longShare -2.5 ast -1.5
CP3|Chris Paul=Chris Paul|ast 2.5 tov -2 stl 2 midFG 1 pullup 1
Griffin|Blake Griffin=Griffin|rimFG 2 pts 1.5 assisted 2 reb 1.5 putback 1 longShare -2 usg 1.5
DeAndre|DeAndre Jordan=DeAndre Jordan|rimFG 2.5 reb 2.5 blk 2 assisted 2.5 usg -2 longShare -2.5 ast -2 putback 1.5
Redick|J.J. Redick=Redick|longShare 2 longFG 2 catch 2 motor 2 assisted 2 reb -1.5 stl -1 ast -0.5
Stockton|John Stockton=Stockton|ast 2.5 stl 2 tov 0.5 usg -1.5 eff 1 assisted -1
Malone|Karl Malone=Malone|pts 2 usg 2 assisted 2 midFG 1.5 reb 1.5 rimFG 1 sast 1
Hornacek|Jeff Hornacek=Hornacek|longFG 1.5 eff 1.5 catch 1 midFG 1 tov -1 reb -1 usg -0.5
Lowry|Kyle Lowry=Lowry|ast 1.5 longShare 1.5 sast 1.5 motor 1.5 usg -0.5 pts -0.5 win 1 stl 1
Siakam|Pascal Siakam=Siakam|drive 1.5 rimFG 1 motor 1.5 reb 1 pts 1 longFG -0.5 usg 0.5
MGasol|Marc Gasol=Marc Gasol|ast 1.5 sast 1.5 blk 1 reb 1 usg -1.5 pts -1 motor -1 win 1
SGA|Shai Gilgeous-Alexander=SGA|usg 2 pts 2.5 pullup 2 midFG 1.5 drive 1.5 stl 1.5 eff 1 win 2
JDub|Jalen Williams=J-Dub|stl 1 drive 1 ast 0.5 pts 0.5 eff 0.5 win 2 reb 0.5 catch 0.5
Chet|Chet Holmgren=Holmgren|blk 2.5 reb 1 longShare 0.5 catch 1 eff 1 usg -0.5 ast -1 win 2
Dort|Luguentz Dort=Dort|stl 1.5 longShare 1.5 catch 1.5 usg -1.5 pts -1 ast -1.5 motor 1.5 win 2
Hartenstein|Isaiah Hartenstein=Hartenstein|reb 2 oreb 1.5 ast 1 sast 2 blk 1 usg -1.5 longShare -2.5 win 2
Billups|Chauncey Billups=Billups|clutch 2 longShare 1 ast 1.5 tov -1 pts 1 win 1.5
BigBen|Ben Wallace=Big Ben|blk 2 reb 2.5 oreb 1.5 stl 1 usg -2 pts -2 longShare -2.5 win 1.5
Rip|Richard Hamilton=Rip Hamilton|midFG 2 catch 1.5 assisted 2 motor 2.5 pts 1 longShare -1 reb -1
Prince|Tayshaun Prince=Prince|blk 1 stl 0.5 usg -1 tov -1 catch 0.5 win 1.5 midFG 0.5
Sheed|Rasheed Wallace=Rasheed Wallace|blk 1.5 longShare 1 midFG 1 reb 1 sast 1 tov 0.5 win 1.5
Webber|Chris Webber=Webber|ast 1.5 reb 2 midFG 1.5 pts 1.5 usg 1.5 blk 1 clutch -1
Bibby|Mike Bibby=Bibby|clutch 2 longFG 1 pullup 1 ast 1 reb -1.5 stl -0.5
Peja|Peja Stojaković=Peja|longShare 2 longFG 2 catch 2 assisted 1.5 motor 1 ast -1 drive -1.5
Divac|Vlade Divac=Divac|ast 1.5 sast 1 reb 1 usg -0.5 motor -1 blk 0.5 longShare -1.5
Christie|Doug Christie=Christie|stl 2 ast 0.5 usg -1 tov 0.5 win 1
TimH|Tim Hardaway=Tim Hardaway|drive 2 ast 2 usg 1.5 pullup 1.5 tov 1 longShare 1
Richmond|Mitch Richmond=Richmond|pts 2 usg 1.5 longFG 1 drive 1 midFG 1
Mullin|Chris Mullin=Mullin|eff 2 longFG 1.5 catch 1 pts 1.5 ast 1 stl 1 motor 1 blk -1
Payton|Gary Payton=Payton|stl 2.5 ast 2 usg 1 pts 1 drive 1
Kemp|Shawn Kemp=Kemp|rimFG 2 putback 1.5 oreb 1.5 reb 2 blk 1.5 assisted 1.5 tov 1 longShare -2
Schrempf|Detlef Schrempf=Schrempf|eff 1.5 longFG 1 ast 1 reb 1 midFG 1
AD|Anthony Davis=Davis|blk 2.5 reb 2 rimFG 1.5 pts 1.5 assisted 1.5 stl 1 putback 1
`,
  hold: `
Bulls 1996|Scoreren, altmuligmanden og rebound-maskinen|MJ Pippen Rodman
Warriors 2017|Tre skytter, som ingen kan dække på én gang|Curry Klay KD
Warriors 2015|To skytter og ham, der binder det hele sammen|Curry Klay Draymond
Heat 2012|Big Three: to, der angriber kurven, og en stor mand med skud|LeBron Wade Bosh
Celtics 2008|Scoreren, forsvarets hjerte og skytten|Pierce KG RayAllen
Spurs 2005|Fundamentet, farten og jokeren|Duncan Parker Manu
Celtics 1986|Den mest komplette frontlinje|Bird McHale Parish
Lakers 1987|Showtime: playmakeren, centeren og ham, der løber kontraerne|Magic Kareem Worthy
Cavaliers 2016|Alt-i-en-spilleren, en-mod-en-scoreren og rebounderen med skud|LeBron Kyrie Love
Thunder 2012|Tre unge scorere på samme hold|KD Westbrook Harden12
Lakers 2001|Kraft under kurven, en scorer og en kold rollespiller|Shaq Kobe Fisher
Pistons 1989|Bad Boys: dirigenten, forsvareren og den hårde center|Isiah Dumars Laimbeer
Rockets 1995|Posten, glideren og clutch-skytten|Hakeem Drexler Horry
Suns 2005|Fart, oplæg og afslutninger på få sekunder|Nash Amare Marion
Nuggets 2023|Alt går gennem den store mand|Jokic Murray Gordon
Bucks 2021|Kraft mod kurven, en stille skytte og en forsvarsguard|Giannis Middleton Holiday
Celtics 2024|To wings og den kloge rollespiller|Tatum Brown White
Mavericks 2011|Mellemdistance-mesteren, skytten og den gamle dirigent|Dirk Terry Kidd
Clippers 2014|Lob City: oplæg og afslutninger over ringen|CP3 Griffin DeAndre
Jazz 1997|Aflevering, afslutning og en skytte ved siden af|Stockton Malone Hornacek
Raptors 2019|Den tavse scorer, organisatoren og energien|Kawhi19 Lowry Siakam
Thunder 2025|Scoreren, den alsidige makker og kurvens vogter|SGA JDub Chet
Pistons 2004|Ingen stjerne, alle arbejder|Billups Rip BigBen
Warriors 1991|Run TMC: tre, der vil løbe og skyde|TimH Richmond Mullin
Kings 2002|Holdet, hvor alle afleverer|Webber Bibby Peja
Nets 2021|Tre, der alle kan score helt alene|KD Harden18 Kyrie
Sonics 1996|Forsvarsguarden, ham over ringen og den effektive veteran|Payton Kemp Schrempf
Lakers 2020|Playmakeren, storspilleren og en rollespiller, der dækker op|LeBron AD KCP
Bulls 1996|Scoreren, altmuligmanden, rebound-maskinen og jokeren fra bænken|MJ Pippen Rodman Kukoc
Warriors 2017|Tre skytter og ham, der binder det hele sammen|Curry Klay KD Draymond
Warriors 2015|To skytter, limen og forsvareren, der kan dække alle|Curry Klay Draymond Iguodala
Heat 2013|Big Three og en skytte i hjørnet|LeBron Wade Bosh RayAllen
Celtics 2008|Scoreren, forsvarets hjerte, skytten og den unge playmaker|Pierce KG RayAllen Rondo
Spurs 2014|Boldbevægelse: alle rører bolden, den bedste chance tager skuddet|Duncan Parker Manu Kawhi14
Lakers 1987|Showtime med en skytte på kanten|Magic Kareem Worthy Scott
Celtics 1986|Den komplette frontlinje og en guard til de store øjeblikke|Bird McHale Parish DJ
Pistons 2004|Ingen stjerne, alle arbejder|Billups Rip Prince BigBen
Pistons 1989|Bad Boys: hårdt forsvar og rebounds|Isiah Dumars Laimbeer Rodman
Suns 2005|Fart, oplæg og skytter hele vejen rundt|Nash Amare Marion JJ
Nuggets 2023|Alt går gennem den store mand, resten afslutter|Jokic Murray Gordon MPJ
Bucks 2021|Kraft mod kurven, en skytte, en forsvarsguard og en mur|Giannis Middleton Holiday Lopez
Celtics 2024|To wings og to guards, der gør alt det rigtige|Tatum Brown White Holiday
Mavericks 2011|Mellemdistance-mesteren og tre, der kender deres rolle|Dirk Terry Kidd Chandler
Thunder 2025|Scoreren og tre, der forsvarer|SGA JDub Chet Dort
Lakers 2001|Kraft, en scorer og to kolde rollespillere|Shaq Kobe Fisher Horry
Rockets 1995|Posten i midten og skytter rundt om|Hakeem Drexler Horry KSmith
Cavaliers 2016|Stjernen, en-mod-en-scoreren og to, der tager rebounds|LeBron Kyrie Love TT
Kings 2002|Holdet, hvor alle afleverer|Webber Bibby Peja Divac
Raptors 2019|Den tavse scorer og tre, der arbejder|Kawhi19 Lowry Siakam MGasol
Clippers 2014|Lob City med en skytte, der aldrig står stille|CP3 Griffin DeAndre Redick
Thunder 2012|Tre unge scorere og en skudblokker|KD Westbrook Harden12 Ibaka
Bulls 1996|72 sejre: scoreren, altmuligmanden, rebound-maskinen og to, der passer deres arbejde|Harper MJ Pippen Rodman Longley
Warriors 2017|Tre skytter, limen og forsvareren|Curry Klay KD Draymond Iguodala
Warriors 2015|Death Lineup: fem, der alle kan skyde, aflevere og skifte i forsvaret|Curry Klay Barnes Draymond Iguodala
Heat 2013|Big Three, en skytte og en guard, der tør|Chalmers Wade LeBron Bosh RayAllen
Celtics 2008|Tre stjerner, en ung playmaker og en mur|Rondo RayAllen Pierce KG Perkins
Spurs 2014|Boldbevægelse: alle rører bolden, den bedste chance tager skuddet|Parker DGreen Kawhi14 Duncan Manu
Lakers 1987|Showtime|Magic Scott Worthy ACGreen Kareem
Celtics 1986|Den komplette frontlinje og to guards, der kæmper|DJ Ainge Bird McHale Parish
Pistons 2004|Ingen stjerne, fem der arbejder|Billups Rip Prince Sheed BigBen
Pistons 1989|Bad Boys|Isiah Dumars Aguirre Rodman Laimbeer
Suns 2005|Fart, oplæg og skytter hele vejen rundt|Nash JJ QRich Marion Amare
Nuggets 2023|Alt går gennem den store mand, resten afslutter|Murray KCP MPJ Gordon Jokic
Bucks 2021|Kraft mod kurven og fire, der gør det beskidte arbejde|Holiday Middleton Giannis Tucker Lopez
Celtics 2024|Fem, der alle kan skyde og forsvare|Holiday White Brown Tatum Porzingis
Mavericks 2011|Mellemdistance-mesteren og fire, der kender deres rolle|Kidd Terry Marion Dirk Chandler
Thunder 2025|Scoreren og fire, der forsvarer|SGA Dort JDub Chet Hartenstein
Lakers 2001|Kraft, en scorer og tre kolde rollespillere|Fisher Kobe Fox Horry Shaq
Rockets 1995|Posten i midten og skytter rundt om|KSmith Cassell Drexler Horry Hakeem
Cavaliers 2016|Stjernen, en-mod-en-scoreren og tre rollespillere|Kyrie JRSmith LeBron Love TT
Kings 2002|Holdet, hvor alle afleverer|Bibby Christie Peja Webber Divac
Raptors 2019|Den tavse scorer og fire, der arbejder|Lowry DGreen Kawhi19 Siakam MGasol
Thunder 2012|Tre unge scorere, en skudblokker og en mur|Westbrook Harden12 KD Ibaka Perkins
`,
};
