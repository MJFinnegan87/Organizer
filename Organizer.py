import wx
import datetime
from pytz import timezone
from pytz import all_timezones
import time
import math

class Frame(wx.Frame):
    def __init__(self, parent, title, windowWidth, windowHeight):
        super(Frame, self).__init__(parent, title=title, 
            size=(windowWidth, windowHeight), style=wx.NO_BORDER)# | wx.STAY_ON_TOP)
        self.justLoading = True
        self.windowWidth = windowWidth
        self.windowHeight = windowHeight
        self.mouseOver = True

        self.calendarDayDisplayArray = [[]]

        self.black = (0,0,0) 
        #self.display_width = int(3*(self.clockWidth+self.clockMargin))+self.clockMargin
        #self.display_height = 768

        self.bgColorMouseOver = (15, 15, 15)
        self.fgColorMouseOver = (255, 255, 255)
        self.bgColorMouseAway = (15, 15, 15)
        self.fgColorMouseAway = (255, 255, 255)
        
        self.SetBackgroundColour(self.bgColorMouseOver)
        self.mostOpaqueLevel = 254 #254
        self.leastOpaqueLevel = 164 #212
        self.alphaTransparency = self.leastOpaqueLevel
        self.clockRefreshSpeed = 1000
        self.transparencyChangeAmount = 1
        self.SetBackgroundColour(self.bgColorMouseOver)
        self.displayTitleBar = False
        self.tzArray = ['America/Los_Angeles', 'America/New_York', 'Europe/London']
        self.tzDescArray = ["Seattle", "New York", "London"]
        self.numberOfClocks = len(self.tzArray)
        self.changeAlpha_timer = wx.Timer(self)
        self.changeAlpha_timer.Start(self.clockRefreshSpeed)

        self.appClocks =[]
        for i in xrange(self.numberOfClocks):
            self.appClocks.append(clock(self.tzArray[i], self.tzDescArray[i]))
        del self.tzArray
        del self.tzDescArray

        #self.Bind(wx.EVT_LEAVE_WINDOW, self.mouseAway) #THIS WAY, CLICKING WINDOW TEXT DOESN'T RESULT IN TRANSPARENT WINDOW
        self.Bind(wx.EVT_KILL_FOCUS, self.mouseAway)
        #self.Bind(wx.EVT_ENTER_WINDOW, self.mouseReturn) #THIS WAY, CLICKING WINDOW TEXT DOESN'T RESULT IN TRANSPARENT WINDOW
        self.Bind(wx.EVT_SET_FOCUS, self.mouseReturn)
        self.Bind(wx.EVT_LEFT_DCLICK, self.toggleTitleBar)
        self.Bind(wx.EVT_CLOSE, self.closeWindow)
        self.Bind(wx.EVT_MOTION, self.mouseMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.leftDown)
        
        self.Bind(wx.EVT_TIMER, self.updateAndDrawClocks)
        self.lastMouseClickPos = (0,0)
        self.justLoading = False
        self.Centre()
        self.Show()
        self.myCal = calendar()
        self.myCal.determineDays(self)
        self.drawCalendar(self.myCal)
        self.updateAndDrawClocks()
        self.drawClockText(self.appClocks)
        
        self.myArray = []
        self.myArray.append(frameText(self, "Title", 500, 10, (255,255,255), "C", "T", None))
        self.myArray[0].Bind(wx.EVT_LEFT_DOWN, self.titleClick)

        #for zone in all_timezones:
        #    print zone

    def titleClick(self, e=None):
        pass

    def selectFirstClockTimeZone(self, e=None):
        self.appClocks[0].updateTimeZone(self.selectFromAllTimeZones(1))
        self.drawClockText(self.appClocks)

    def selectSecondClockTimeZone(self, e=None):
        self.appClocks[1].updateTimeZone(self.selectFromAllTimeZones(2))
        self.drawClockText(self.appClocks)

    def selectThirdClockTimeZone(self, e=None):
        self.appClocks[2].updateTimeZone(self.selectFromAllTimeZones(3))
        self.drawClockText(self.appClocks)
        
    def selectFromAllTimeZones(self, clockSelection):
        if self.justLoading == False:
            listOfAvailableTimeZones = []
            for zone in all_timezones:
                listOfAvailableTimeZones.append(zone)
            chooseOneBox = wx.SingleChoiceDialog(None, "What time zone should this clock show?", "Time Zone Selection", listOfAvailableTimeZones)
            if chooseOneBox.ShowModal() == wx.ID_OK:
                selTimeZone = chooseOneBox.GetStringSelection()
        return selTimeZone

    def drawClockText(self, displayClocks):
        try:
            self.timeZoneCityLabel1.Destroy()
            self.timeZoneCityLabel2.Destroy()
            self.timeZoneCityLabel3.Destroy()
        except:
            pass
        self.timeZoneCityLabel1 = frameText(self, displayClocks[0].tzDesc, 0*3*(displayClocks[0].clockWidth+displayClocks[0].clockMargin)/float(3) + displayClocks[0].clockX, displayClocks[0].clockY, self.fgColorMouseOver, "C", "C",  displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.timeZoneCityLabel2 = frameText(self, displayClocks[1].tzDesc, 1*3*(displayClocks[1].clockWidth+displayClocks[1].clockMargin)/float(3) + displayClocks[1].clockX, displayClocks[1].clockY, self.fgColorMouseOver, "C", "C",  displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.timeZoneCityLabel3 = frameText(self, displayClocks[2].tzDesc, 2*3*(displayClocks[2].clockWidth+displayClocks[2].clockMargin)/float(3) + displayClocks[2].clockX, displayClocks[2].clockY, self.fgColorMouseOver, "C", "C", displayFont=wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        self.timeZoneCityLabel1.Bind(wx.EVT_LEFT_DCLICK, self.selectFirstClockTimeZone)
        self.timeZoneCityLabel2.Bind(wx.EVT_LEFT_DCLICK, self.selectSecondClockTimeZone)
        self.timeZoneCityLabel3.Bind(wx.EVT_LEFT_DCLICK, self.selectThirdClockTimeZone)
        
    def drawCalendar(self, dispCal):
        for i in xrange(len(dispCal.calDayGrid)):
            for j in xrange(7):
                if dispCal.calDayGrid[i][j][1] != 0:
                    if dispCal.calDayGrid[i][j][1] == "Other Month":
                        rgb = dispCal.otherMonthCalDayColor
                    elif dispCal.calDayGrid[i][j][1] == "This Month":
                        rgb = dispCal.thisMonthCalDayColor
                    elif dispCal.calDayGrid[i][j][1] == "Today":
                        rgb = dispCal.calTodayColor
                    self.displayDay = frameText(self, dispCal.calDayGrid[i][j][0], 700 + 35*j, 40 + 35*i, rgb, "L", "T", None)
                    #self.displayDay.Bind(wx.EVT_LEFT_DOWN, self.calendarDaySelect)
                    self.calendarDayDisplayArray[i].append(self.displayDay)
            self.calendarDayDisplayArray.append([])

        #self.workingDate = wx.StaticText(frame, -1, str(nthDayOfMonth), pos=(700 + 35*((workingDate.weekday() + 1)%7), 40 + 35*jthRow))
        #self.workingDate.SetFont(wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.NORMAL))
        #if (datetime.datetime(datetime.datetime.today().year + yearAdj, datetime.datetime.today().month + workingMonth + prevMonthDec, nthDayOfMonth, 0, 0, 0, 0) == datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 0, 0, 0, 0)):
        #    self.workingDate.SetForegroundColour(self.calTodayColor)
        #else:
        #    if workingMonth == 0:
        #        self.workingDate.SetForegroundColour(self.thisMonthCalDayColor)
        #    else:
        #        self.workingDate.SetForegroundColour(self.otherMonthCalDayColor)
        ##self.workingDate.Bind(wx.EVT_LEFT_DOWN, self.calendarDaySelect)
        #if nthDayOfMonth == 1 and workingMonth == -int(self.numberOfMonths/float(2)):
        #    for i in xrange(workingDate.weekday()):
        #        self.calDayGrid[0].append(0)
        #self.calDayGrid[jthRow].append(nthDayOfMonth)
        #nthDayOfMonth = nthDayOfMonth + 1
        #if workingDate.weekday() == 5 :
        #    jthRow = jthRow + 1
        #    self.calDayGrid.append([])


    def calendarDaySelect(self, e=None):
        print str(self.displayDay)

    def clearDrawings(self):
        dc = wx.ClientDC(self)
        dc.Clear()

    def drawLine(self, x1, y1, x2, y2, strokeWidth,  lineColor):
        dc = wx.ClientDC(self)
        dc.SetPen(wx.Pen(lineColor, strokeWidth))
        dc.DrawLine(x1, y1, x2, y2)

    def mouseAway(self, e):
        #WE WANT TO MAKE BACKGROUND TRANSPARENT ON MOUSE AWAY FROM WINDOW, BUT
        #NOT IF THE MOUSE AWAY IS ACTUALLY MOUSE OVER THE WINDOW'S OWN TEXT
        #if self.mouseOver == False:
        self.SetBackgroundColour(self.bgColorMouseAway)
        self.SetTransparent(self.leastOpaqueLevel)
        self.mouseOver = False
        #self.drawClocks(self.appClocks)
        self.updateAndDrawClocks()
            
    def mouseReturn(self, e):
        #self.SetBackgroundColour(self.bgColorMouseOver)
        self.SetTransparent(self.mostOpaqueLevel)
        self.mouseOver = True
        #self.drawClocks(self.appClocks)
        self.updateAndDrawClocks()

    def mouseMotion(self, e):
        #print str(wx.GetMousePosition())
        if e.LeftIsDown():
            self.Move(wx.Point(wx.GetMousePosition()[0] - self.lastMouseClickPos[0], wx.GetMousePosition()[1] - self.lastMouseClickPos[1]))
        e.Skip()
 
    def leftDown(self, e):
        self.lastMouseClickPos = e.GetPosition()
        e.Skip()

    def toggleTitleBar(self, e):
        if (self.displayTitleBar == True):
            self.style = wx.NO_BORDER
            self.displayTitleBar = False
            self.Show()
            
        elif (self.displayTitleBar == False):
            self.style = wx.SIMPLE_BORDER
            self.displayTitleBar = True
            self.Show()

    def closeWindow(self, e):
        self.changeAlpha_timer.Stop()
        del self.changeAlpha_timer       # avoid a memory leak
        self.Destroy()
        exit()

    def updateAndDrawClocks(self, e = None):
        for i in self.appClocks:
            i.updateTime()
        self.drawClocks(self.appClocks)

    def drawClocks(self, displayClocks):
        #try:
        self.clearDrawings()
        for i in xrange(len(displayClocks)):
            for j in xrange(12):
                self.drawLine(
                int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX + (int(round((displayClocks[i].minuteLength + displayClocks[i].clockTickInnerMargin) * math.cos((math.pi/180)*(((j+1)/float(12)))*360))))),
                int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round((displayClocks[i].minuteLength + displayClocks[i].clockTickInnerMargin) * math.sin((math.pi/180)*(((j+1)/float(12)))*360)))),
                int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX  + (int(round((displayClocks[i].minuteLength + displayClocks[i].clockTickInnerMargin + displayClocks[i].clockTickLength) * math.cos((math.pi/180)*(((j+1)/float(12)))*360))))),
                int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round((displayClocks[i].minuteLength + displayClocks[i].clockTickInnerMargin + displayClocks[i].clockTickLength) * math.sin((math.pi/180)*(((j+1)/float(12)))*360)))), displayClocks[i].tickThick, displayClocks[i].tickColor)

            #DRAW CLOCK HANDS
            #LINE(X1,
            #Y1,
            #X2,
            #Y2,
            #THICKNESS, COLOR)
            
            #DRAW HOUR HAND
            self.drawLine(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX ,
                          displayClocks[i].clockHeight + displayClocks[i].clockMargin,
                          int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX  + (int(round(displayClocks[i].hourLength * math.cos((math.pi/180)*((((displayClocks[i].hours-3)%float(12))/float(12))+(displayClocks[i].minutes/float(60)/12))*360))))),
                          int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round(displayClocks[i].hourLength * math.sin((math.pi/180)*((((displayClocks[i].hours-3)%float(12))/float(12))+(displayClocks[i].minutes/float(60)/12))*360)))),
                          displayClocks[i].hourThick, displayClocks[i].hourColor)
            
            #DRAW MINUTE HAND
            self.drawLine(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX ,
                          displayClocks[i].clockHeight + displayClocks[i].clockMargin,
                          int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX  + (int(round(displayClocks[i].minuteLength * math.cos((math.pi/180)*((displayClocks[i].minutes-15)/float(60))*360))))),
                          int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round(displayClocks[i].minuteLength * math.sin((math.pi/180)*((displayClocks[i].minutes-15)/float(60))*360)))),
                          displayClocks[i].minuteThick, displayClocks[i].minuteColor)

            #DRAW SECOND HAND
            self.drawLine(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX ,
                          displayClocks[i].clockHeight + displayClocks[i].clockMargin,
                          int(i*(displayClocks[i].clockWidth + displayClocks[i].clockMargin) + displayClocks[i].clockX  + (int(round(displayClocks[i].secondLength * math.cos((math.pi/180)*((displayClocks[i].seconds-15)/float(60))*360))))),
                          int(displayClocks[i].clockHeight + displayClocks[i].clockMargin + int(round(displayClocks[i].secondLength * math.sin((math.pi/180)*((displayClocks[i].seconds-15)/float(60))*360)))),
                          displayClocks[i].secondThick, displayClocks[i].secondColor)

class clock(object):
    def __init__(self, tz, tzDesc):
        self.secondColor = (255, 0, 0)
        self.minuteColor = (255, 255, 255)
        self.hourColor = (255, 255, 255)
        self.tickColor = (255, 255, 255)
        self.secondThick = 2
        self.minuteThick = 4
        self.hourThick = 4
        self.tickThick = 2
        self.secondLength = 50
        self.minuteLength = 50
        self.hourLength = .5*self.minuteLength
        self.clockMargin = 15
        self.clockTickLength = 10
        self.clockTickInnerMargin = 8
        self.clockWidth = (self.minuteLength*2) + (self.clockTickLength*2) + (self.clockTickInnerMargin*2)
        self.clockHeight = self.clockWidth
        self.clockX = (self.minuteLength) + (self.clockTickLength) + (self.clockTickInnerMargin) + self.clockMargin
        self.clockY = self.clockHeight / float(4)
        self.tz = tz
        self.tzDesc = tzDesc
        self.tzTime = ""

    def updateTime(self):
        now_utc = datetime.datetime.now(timezone('UTC')) #Put the current time in UTC
        self.seconds = float(now_utc.astimezone(timezone(self.tz)).strftime("%S"))
        self.minutes = float(now_utc.astimezone(timezone(self.tz)).strftime("%M"))
        self.hours = float(now_utc.astimezone(timezone(self.tz)).strftime("%H"))

    def updateTimeZone(self, tz):
        self.tz = tz
        self.tzDesc = self.tz[self.tz.find("/")+1:].replace("_", " ")
        self.updateTime()

class calendar(object):
    def __init__(self):
        self.thisMonthCalDayColor = (255,255,255)
        self.otherMonthCalDayColor = (96,96,96)
        self.calTodayColor = (255,0,0)
        self.numberOfMonths = 3
        self.calDayGrid = []
        self.calDayGrid.append([])

    def determineDays(self, frame):
        nthDayOfMonth = 1
        jthRow = 0
        workingMonth = -int(self.numberOfMonths/float(2))
        while workingMonth <= int(self.numberOfMonths/float(2)):
            if datetime.datetime.today().month + workingMonth < 1:
                prevMonthDec = datetime.datetime.today().month + workingMonth + 12
                yearAdj = -1
            else:
                prevMonthDec = 0
                yearAdj = 0
            try:
                workingDate = datetime.datetime(datetime.datetime.today().year + yearAdj, datetime.datetime.today().month + workingMonth + prevMonthDec, nthDayOfMonth, 0, 0, 0, 0)
                if (datetime.datetime(datetime.datetime.today().year + yearAdj, datetime.datetime.today().month + workingMonth + prevMonthDec, nthDayOfMonth, 0, 0, 0, 0) == datetime.datetime(datetime.datetime.today().year, datetime.datetime.today().month, datetime.datetime.today().day, 0, 0, 0, 0)):
                    dayAttribute = "Today"
                else:
                    if workingMonth == 0:
                        dayAttribute = "This Month"
                    else:
                        dayAttribute = "Other Month"
                if nthDayOfMonth == 1 and workingMonth == -int(self.numberOfMonths/float(2)):
                    for i in xrange(workingDate.weekday() + 1):
                        self.calDayGrid[0].append([0,0])
                self.calDayGrid[jthRow].append([str(nthDayOfMonth), dayAttribute])
                nthDayOfMonth = nthDayOfMonth + 1
                if workingDate.weekday() == 5 :
                    jthRow = jthRow + 1
                    self.calDayGrid.append([])
            except:        
                nthDayOfMonth = 1
                workingMonth = workingMonth + 1
        if workingDate.weekday() != 5:
            for i in xrange(5 - workingDate.weekday()):
                self.calDayGrid[jthRow].append([0,0])

class frameText(wx.StaticText):
    def __init__(self, displayFrame, displayText, x, y, displayColor, alignX, alignY, displayFont):
        super(frameText, self).__init__(displayFrame, -1, displayText)
        dc = wx.ClientDC(displayFrame)
        if displayFont == None:
            displayFont = wx.Font(pointSize = 16, family = wx.DECORATIVE, style = wx.NORMAL, weight = wx.NORMAL)#, faceName = 'Consolas'))
        dc.SetFont(displayFont)
        #self = wx.StaticText(displayFrame, -1, displayText)
        self.SetFont(displayFont)#, faceName = 'Consolas'))
        self.SetForegroundColour(displayColor)
        w,h = dc.GetTextExtent(displayText)        
        if alignX == "C":
            x = x-(w/float(2))
        elif alignX == "R":
            x = x-w
        if alignY == "C":
            y = y-(h/float(2))
        elif alignY == "B":
            y = y-h
        self.SetPosition((int(x), int(y)))
        

        
if __name__ == '__main__':
    app = wx.App()
    myFrame = Frame(None, 'Organizer', 1000, 800)
    app.MainLoop()
