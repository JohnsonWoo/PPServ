#!/usr/bin/env python
# coding:utf-8

import wx
import logging
import logging.config
from module.module_factory import *
from conf import *
from lang import *
from cache import *
from common import *
from message_handler import *
import state_label
import task_bar_icon


class App(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, APPNAME + VERSION, size=(800, 230))
        self.SetIcon(wx.Icon('icon.ico', wx.BITMAP_TYPE_ICO))
        self.taskBarIcon = task_bar_icon.TaskBarIcon(self)
        self.Bind(wx.EVT_CLOSE, self.OnHide)
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
        self.SetBackgroundColour('white')
        self.InitUi()
        self.Center()
        self.Show()

    def InitUi(self):
        self.data = Cache().get()
        self.lbl = {}
        self.btnSize = (110, 25)
        self.mod_list = {}

        for mod in ModuleFactory.get_module_list():
            self.mod_list[mod.module_name] = mod

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.basicPanel = wx.Panel(self, size=self.GetSize())
        self.advtPanel = wx.Panel(self, size=self.GetSize())
        self.advtPanel.Hide()

        self.InitBasicPanel()
        self.InitAdvtPanel()

        self.sizer.Add(self.basicPanel, 1, wx.EXPAND | wx.ALL, 10)
        self.sizer.Add(self.advtPanel, 1, wx.EXPAND | wx.ALL, 0)

        self.SetSizerAndFit(self.sizer)
        self.Start()

    def InitBasicPanel(self):
        self.basicSizer = wx.BoxSizer(wx.VERTICAL)
        self.basicPanel.SetSizer(self.basicSizer)

        self.runBox = wx.StaticBox(self.basicPanel, -1, Lang().get('autorun_label'), name="run_box")
        self.CreateModuleList()

        runBtnSize = (120, 70)
        startAllBtn = wx.Button(self.basicPanel, -1, Lang().get('start_all_service'), size=runBtnSize, name='start')
        stopAllBtn = wx.Button(self.basicPanel, -1, Lang().get('stop_all_service'), size=runBtnSize, name='stop')
        startAllBtn.Bind(wx.EVT_BUTTON, self.BatchHandlerServices)
        stopAllBtn.Bind(wx.EVT_BUTTON, self.BatchHandlerServices)

        runSizer = wx.StaticBoxSizer(self.runBox, wx.HORIZONTAL)
        runSizer.AddMany([
            (self.modSizer, 0, wx.LEFT | wx.RIGHT, 5),
            (startAllBtn, 0, wx.ALL, 10),
            (stopAllBtn, 0, wx.ALL, 10)
        ])

        self.CreateOften()
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        topSizer.Add(runSizer, 0, wx.ALL)
        topSizer.Add(self.oftenSizer, 0, wx.LEFT, 10)
        self.basicSizer.Add(topSizer)

        self.stateBox = wx.TextCtrl(self.basicPanel, -1, "", size=(600, 100), style=wx.TE_MULTILINE)
        self.bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.bottomSizer.Add(self.stateBox, 1, wx.ALL | wx.EXPAND, 5)
        self.basicSizer.Add(self.stateBox, 1, wx.EXPAND | wx.TOP, 5)

    def InitAdvtPanel(self):
        self.advtSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.advtPanel.SetSizer(self.advtSizer)

        self.advtTab = wx.Notebook(self.advtPanel)
        self.advtSizer.Add(self.advtTab, -1, wx.EXPAND | wx.RIGHT, 5)
        for mod_name, mod in self.mod_list.items():
            mod.set_advt_frame(self.advtTab)

        self.advtBox = wx.StaticBox(self.advtPanel, -1, Lang().get('often_label'))
        self.advtOftenSizer = wx.StaticBoxSizer(self.advtBox, wx.VERTICAL)

        basicBtn = wx.Button(self.advtPanel, -1, Lang().get('basic_setting'), size=self.btnSize, name='basic')
        basicBtn.Bind(wx.EVT_BUTTON, self.Toggle)

        cmdBtn = wx.Button(self.advtPanel, -1, Lang().get('open_cmd'), size=self.btnSize)
        cmdBtn.Bind(wx.EVT_BUTTON, self.OpenCmd)

        self.advtOftenSizer.AddMany([
            (basicBtn, 1, wx.EXPAND | wx.ALL, 5),
            (cmdBtn, 1, wx.EXPAND | wx.ALL, 5)
        ])
        self.advtSizer.Add(self.advtOftenSizer, 0, wx.RIGHT, 5)

    def CreateOften(self):
        oftenBox = wx.StaticBox(self.basicPanel, -1, Lang().get('often_label'), name="often_box")
        self.oftenSizer = wx.StaticBoxSizer(oftenBox, wx.VERTICAL)
        self.oftenBtnSizer = wx.FlexGridSizer(rows=5, cols=2)

        oftenData = (('edit_hosts', open_hosts),
                     ('addto_startup', set_autorun),
                     ('advt_setting', self.Toggle))

        for label, handler in oftenData:
            oftenBtn = wx.Button(self.basicPanel, -1, Lang().get(label), size=self.btnSize, name=label)
            oftenBtn.Bind(wx.EVT_BUTTON, handler)
            self.oftenBtnSizer.Add(oftenBtn, 0, wx.ALL, 5)
        self.oftenSizer.Add(self.oftenBtnSizer)

    def CreateModuleList(self):
        self.modSizer = wx.FlexGridSizer(rows=5, cols=2)
        for module_name in BaseModule.list_service_module():
            run = wx.CheckBox(self.basicPanel, -1, module_name, size=[120, 13])
            run.SetValue(run.Label in self.data['autorun'] and self.data['autorun'][run.Label])
            run.Bind(wx.EVT_CHECKBOX, self.SaveSelect)

            self.lbl[module_name] = state_label.StateLabel(self.basicPanel, -1, "stop", size=(50, 15), mappingData=module_name)
            self.modSizer.Add(run, 0, wx.ALL, 5)
            self.modSizer.Add(self.lbl[module_name], 0, wx.ALL, 5)

    def OnHide(self, event):
        """隐藏"""
        self.Hide()

    def OnIconfiy(self, event):
        """点击关闭时只退出监控界面"""
        self.Hide()
        event.Skip()

    def OnClose(self, event):
        """退出"""
        self.taskBarIcon.Destroy()
        self.Destroy()

    def SaveSelect(self, event):
        """保存选中的自动运行的程序的状态"""
        sender = event.GetEventObject()
        self.data['autorun'][sender.Label] = sender.GetValue()
        Cache().set("autorun", self.data['autorun'])

    def Start(self):
        self.SetLog()
        wx.CallAfter(self.UpdateState)

    def UpdateState(self):
        """自动更新各模块的状态显示"""
        for module_name in BaseModule.list_service_module():
            mod = self.mod_list[module_name]
            if mod.is_install():
                self.lbl[module_name].SetLabel(mod.get_state().lower())
            else:
                mod.install_service()
        wx.CallLater(3000, self.UpdateState)

    def SetLog(self):
        #从配置文件中设置log
        logging.config.dictConfig(Conf().get('logging'))

        handler = MessageHandler(self.stateBox)
        log = logging.getLogger()
        log.addHandler(handler)
        log.setLevel(logging.INFO)

    def BatchHandlerServices(self, event):
        """批量处理各模块启动或停止服务"""
        for module_name, state in Cache().get("autorun").items():
            if state:
                mod = self.mod_list[module_name]
                if event.GetEventObject().GetName() == "start":
                    wx.CallAfter(mod.start_service)
                else:
                    wx.CallAfter(mod.stop_service)

    def Toggle(self, event):
        #保持Panel和Frame的大小一致
        self.basicPanel.SetSize(self.GetSize())
        self.advtPanel.SetSize(self.GetSize())
        if event.GetEventObject().GetName() == 'basic':
            self.basicPanel.Show()
            self.advtPanel.Hide()
        else:
            self.basicPanel.Hide()
            self.advtPanel.Show()

    def OpenCmd(self, event):
        tabName = self.advtTab.GetPageText(self.advtTab.GetSelection())
        open_cmd(self.mod_list[tabName].path)


app = wx.App()
frame = App()
app.MainLoop()
