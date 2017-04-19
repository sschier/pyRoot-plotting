#!/usr/bin/env python

#IMPORTS
import ROOT
import sys, copy, os
import argparse, subprocess, commands
import math

#GLOBAL VARIABLES
logYAxis = True

#ATLAS STYLE
ROOT.gROOT.LoadMacro("/export/home/prose/myPrograms/scripts/atlasstyle-00-03-05/AtlasUtils.C")
ROOT.gROOT.LoadMacro("/export/home/prose/myPrograms/scripts/atlasstyle-00-03-05/AtlasStyle.C")
ROOT.gROOT.LoadMacro("/export/home/prose/myPrograms/scripts/atlasstyle-00-03-05/AtlasLabels.C")
ROOT.SetAtlasStyle()

mc_names = ['zjets'] 
data_names = ['data']
signal_names = ['991500', '991502']
#ROOT.gROOT.SetBatch(True)
#======================================================================
def GetRootFiles(dir, debug):
    file_list = []
    if not dir.endswith("/"): dir = dir + "/"
    #status, files = commands.getstatusoutput('ls ' + dir)
    files = commands.getoutput('ls ' + dir)
    files = files.split("\n")
    for f in files:
        if f.endswith(".root"): file_list += [dir + f]
    if debug: 
        #print dir
        print file_list
    return file_list
#======================================================================
def GetDataHists(file_list, hist_path, debug):
    if debug: print 'getting data hists'
    print file_list
    #hists = []
    iter = 0
    for name in file_list:
        print IsData(name)
        if IsData(name):
            f = ROOT.TFile(name, 'READ')
            keys = f.GetListOfKeys()
            if debug:
                print f.GetName()
                print 'list of keys = '
                #for k in keys:
                #    print k.GetName()
            h = f.Get(hist_path)
            isTH1 = True
            try: isTH1 = 'TH1' in h.ClassName()
            except: 
                isTH1 = False
            if not isTH1:
                f.Close()
                continue
            h.SetDirectory(0)
            #hists.append(copy.deepcopy(h))
            #hists[iter].SetDirectory(0)
            f.Close()
            iter = iter + 1

    return h


#======================================================================
def GetSignalHists(file_list, hist_path, debug):
    if debug: print 'getting mc hists'
    hists = []
    iter = 0
    for name in file_list:
        print IsSignal(name)
        if IsSignal(name):
            f = ROOT.TFile(name, 'READ')
            if debug: print 'file is %s' % f
           # keys = f.GetListOfKeys()
           # if debug:
           #     print f.GetName()
           #     print 'list of keys = '
           #     for k in keys:
           #         print k.GetName()
            h = f.Get(hist_path)
            isTH1 = True
            try: isTH1 = 'TH1' in h.ClassName()
            except: 
                isTH1 = False
            if not isTH1:
                f.Close()
                continue
            h.SetDirectory(0)
            hists.append(copy.deepcopy(h))
            hists[iter].SetDirectory(0)
            f.Close()
            iter = iter + 1

    if debug:
        for h in hists:
            print h
    return hists

#======================================================================
#======================================================================
def IsSignal(file_name):
    isSignal = False
    name = file_name.replace('.root', '').split('/')[-1].split('_')
    print name
    for n in name:
        if n in signal_names:
            isSignal =  True
    return isSignal    

#======================================================================
#======================================================================
def IsData(file_name):
    isData = False
    name = file_name.replace('.root', '').split('/')[-1].split('_')
    print name
    for n in name:
        if n in data_names:
            isData =  True
        print isData
    return isData    

#======================================================================

#======================================================================
def GetNameFromFileName(file_name_str):

    dsid = file_name_str.replace('.root', '').split('/')[-1].split('_')[1]
    return dsid
#======================================================================
def IsBkgnd(file_name):
    isBkgnd = False
    name = file_name.replace('.root', '').split('/')[-1].split('_')
    for n in name:
        if n in mc_names:
            isBkgnd =  True
    return isBkgnd    

#======================================================================
def SumMCHists(hist_list):
    print 'in SumMC'
    print hist_list
    sortedHistTuple = sorted(hist_list.items(), key=lambda x: x[1].GetBinContent(x[1].GetMaximumBin()))
    base = ROOT.TH1F('base', '',5, 250., 700)
    for h, x in zip(sortedHistTuple, xrange(10)):
        h[1].SetDirectory(0)
        if x is 0:
            base = copy.deepcopy(h[1])
            base.SetDirectory(0)
        else:
            base.Add(h[1])
    return base
#======================================================================
def GetMCHists(file_list, hist_path, debug):
    if debug: print 'getting mc hists'
    hists = {}
    for string in file_list:
        name = GetNameFromFileName(string)
        print '***************'
        print name
        print '**************'
        if debug: print IsBkgnd(string)
        if IsBkgnd(string):
            f = ROOT.TFile(string, 'READ')
            if debug: print 'file is %s' % f
            h = f.Get(hist_path)
            isTH1 = True
            try: isTH1 = 'TH1' in h.ClassName()
            except: 
                isTH1 = False
            if not isTH1:
                f.Close()
                continue
            h.SetDirectory(0)
            hists[name] = copy.deepcopy(h)
            hists[name].SetDirectory(0)
            f.Close()

    if debug:
        for k in hists:
            print hists[k]
    return hists
#======================================================================
def MakeHistStack(hist_list, debug):
    hs = ROOT.THStack("hist stack", "hist stack")
    factor1 = 0.799
    factor2 = 1.799
    factor3 = 1.924
    factor4 = 3.467
    factor5 = 4.625
    #sortedHistTuple = sorted(hists,
    sortedHistTuple = sorted(hist_list.items(), key=lambda x: x[1].GetBinContent(x[1].GetMaximumBin()))
    print 'in MakeMC'
    print hist_list
    print sortedHistTuple
    sortedKeyList = sorted(hist_list.keys())
    colors = [7, 5]  #[yellow, Lgreen, Dgreen, red, blue, cyan, indigo, purple, magenta]
    markers = [33, 35]     #[diamond, cross, circle, square, star, cross-hair, triangleup, opentriangledown, open-square
    colormap = {}
    markermap = {}
    for k, c, m in zip(sortedKeyList, colors, markers):
        colormap[k] = c
        markermap[k] = m
    if debug: print colormap

    for h in sortedHistTuple:
        if debug: print "adding hist to stack"
        #hist = h.Clone("hist")
        h[1].SetFillColor(colormap[h[0]])
        h[1].SetMarkerColor(colormap[h[0]])
        h[1].SetMarkerStyle(markermap[h[0]])
        h[1].SetMarkerSize()
        #h[1].Scale(factor5)
        h[1].SetDirectory(0)
        hs.Add(h[1])
    return hs

#======================================================================
def DataCanvas(region):
    global logYAxis
    c2 = ROOT.TCanvas("data_%s" % region, "data_%s" % region, 0, 0, 600, 600)
    #c1.Divide(1,2,0,0)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1.0)
    p1.SetBottomMargin(0)
    if logYAxis: p1.SetLogy(ROOT.kTRUE)
    c2.cd(1)
    p1.Draw()

    return c2, p1
#======================================================================
def SetRatioCanvas(name, region):
    global logYAxis
    c1 = ROOT.TCanvas("%s_%s" % (name, region), "%s_%s" % (name, region), 0, 0, 800, 600)
    #c1.Divide(1,2,0,0)
    p1 = ROOT.TPad("p1", "p1", 0, 0.35, 1, 1.0)
    p1.SetBottomMargin(0.01)
    if logYAxis: p1.SetLogy(ROOT.kTRUE)
    c1.cd(1)
    p1.Draw()
    primarytextscale=1./(p1.GetWh()*p1.GetAbsHNDC());
    p2 = ROOT.TPad("p2", "p2", 0, 0.0, 1, 0.344)
    p2.SetTopMargin(0.05)
    p2.SetBottomMargin(0.37)
    c1.cd(2)
    p2.Draw()
    ratiotextscale=1./(p2.GetWh()*p2.GetAbsHNDC());

    return c1, p1, p2

#======================================================================
def SetCanvas(name, region):
    global logYAxis
    c1 = ROOT.TCanvas("%s_%s" % (name, region), "%s_%s" % (name, region), 0, 0, 600, 600)
    #c1.Divide(1,2,0,0)
    p1 = ROOT.TPad("p1", "p1", 0, 0.3, 1, 1.0)
    p1.SetBottomMargin(0)
    if logYAxis: p1.SetLogy(ROOT.kTRUE)
    c1.cd(1)
    p1.Draw()
    p2 = ROOT.TPad("p2", "p2", 0, 0.0, 1, 0.3)
    p2.SetTopMargin(0)
    p2.SetBottomMargin(0.3)
    c1.cd(2)
    p2.Draw()

    return c1, p1, p2

#======================================================================
def MakeLegend(bkgndHists, dataHist, region):

    #sortedHistTuple = sorted(bkgndHists, key=lambda x: x.GetBinContent(x.GetMaximumBin()))
    sortedHistTuple = sorted(bkgndHists.items(), key=lambda x: x[1].GetBinContent(x[1].GetMaximumBin()), reverse=True)

    l = ROOT.TLegend(0.8, 0.8, 0.91, 0.95)
    for hist in sortedHistTuple:
        l.AddEntry(hist[1], hist[0], 'f')
    #for hist, name in zip(sortedHistTuple, samples):
    #    l.AddEntry(hist, name, 'f')
    l.AddEntry(dataHist, 'data', 'l')

    return l

#======================================================================
def MakeNewRatio(topHist, bottomHist):

    rh = copy.deepcopy(topHist)
    rh.SetDirectory(0)
    rh.Divide(bottomHist)
    rh.SetMinimum(0)
    rh.SetMaximum(2)
    title = str(bottomHist.GetXaxis().GetTitle())
    print '*****'
    #print bottomHist.GetXaxis().GetTitle()
    #rh.GetXaxis().SetTitle(str(bottomHist.GetXaxis().GetTitle()))
    print topHist.GetXaxis().GetTitle()
    rh.GetXaxis().SetTitle(str(topHist.GetXaxis().GetTitle()))
    #if bottomHist == 'lep_type':
    #    rh.GetXaxis().SetBinLabel(2,(str(bottomHist.GetXaxis().GetBinLabel(2))))
    #    rh.GetXaxis().SetBinLabel(3,(str(bottomHist.GetXaxis().GetBinLabel(3))))
    rh.GetXaxis().SetLabelSize(0.12)
    rh.GetYaxis().SetLabelSize(0.12)
    rh.GetYaxis().SetNdivisions(8)
    rh.GetXaxis().SetTitleSize(0.16)
    rh.GetYaxis().SetTitleSize(0.16)
    rh.GetXaxis().SetTitleOffset(0.9)
    rh.GetYaxis().SetTitleOffset(0.39)
    rh.GetYaxis().SetTitle("Data/MC")

    #zeroline=rh.TLine(0, 1.0, xmax, 1.0)
    #zeroline.SetLineWidth(2)
    #zeroline.Draw()

    return rh
#======================================================================
def MakeRatio(bkgndHist, dataHist):

    rh = copy.deepcopy(dataHist)
    rh.SetDirectory(0)
    rh.Divide(bkgndHist)
    rh.SetMinimum(0.5)
    rh.SetMaximum(1.5)

    return rh
#======================================================================
def plot(sample_path, region, variable, indir, debug):
    if debug: print "opening output file"
    o=ROOT.TFile("test.root", "RECREATE")
    print "Setting variable to plot"
    var = variable
    print "Getting MC list"
    MChist_list = GetMCHists(GetRootFiles(indir, 0), sample_path, debug)
    print "Getting data hist"
    m_data = GetDataHists(GetRootFiles(indir, 0), sample_path, debug)
    print "Making MC hist stack"
    m_hstack = MakeHistStack(MChist_list, debug)
    m_hsum = SumMCHists(MChist_list)
    m_ratio = MakeNewRatio(m_data, m_hsum)
    m_legend = MakeLegend(MChist_list, m_data, region)
    #canvas, p1, p2 = SetCanvas('%s' % var, region)
    canvas, p1, p2 = SetRatioCanvas('canvas', region)
    p2.cd()
    m_ratio.Draw("P")
    #m_line.Draw("SAME")
    p1.cd()
    m_hstack.Draw("HIST")
    m_data.Draw("PESAME")
    o.cd()
    m_hstack.Write()
    canvas.Write()

    canvas.cd()
    m_legend.Draw()
    ROOT.gStyle.SetLegendBorderSize(0)
    ROOT.gROOT.ForceStyle()
    #ROOT.myText(       0.41,  0.85, 1, "2.5fb^{-1}@ #sqrt{s}= 13 TeV")
    #ROOT.myText(       0.41,  0.80, 1, "data16PeriodK")
    #ROOT.myText(       0.41,  0.85, 1, "%s" % region)
    ROOT.ATLASLabel(0.41,0.90,"Internal")
    #canvas.Print('%s.png' % sample_path)
    #c2, p3 = DataCanvas(region)
    #m_data.Draw()
    raw_input("-->")
    canvas.Print('%s_%s.pdf' % (region, var))
    return True
#======================================================================
def main(argv):

    parser = argparse.ArgumentParser(description="Command line arguments")
    parser.add_argument("-vars"          , action='store', default='')
    parser.add_argument("-indir"        , action='store', default='')
    parser.add_argument("-outfile"      , action='store', default='')
    parser.add_argument("--test"        , action='store_true')
    parser.add_argument("-region"       , action='store', default="SR")
    args=parser.parse_args()

    print "Congratulations!"
    var_list = []
    variables4 = ['MET', 'Lep1Pt', 'Lep2Pt', 'Jet1Pt', 'Jet2Pt','nLep_signal', 'nJet25', 'mll', 'ptll', 'dphi_l1met', 'dphi_l2met', 'dphi_j1met', 'dphi_j2met', 'dphi_l1l2', 'lep_charge', 'qlql','METoverHt', 'Ht30', 'lep_type', 'Mt', 'Mt_l1met','Mt_l2met', 'MTauTau']
    variables5 = ['MET', 'Lep1Pt', 'Lep2Pt', 'Jet1Pt', 'Jet2Pt','nLep_signal', 'nJet25', 'mll', 'ptll', 'dphi_l1met', 'dphi_l2met', 'dphi_j1met', 'dphi_j2met', 'dphi_l1l2', 'lep_charge', 'qlql','METoverHt', 'Ht30', 'lep_type', 'Mt', 'Mt_l1met','Mt_l2met', 'MTauTau', 'muPt', 'elPt', 'nVtx' ]
    variables6 = ['MET', 'Lep1Pt', 'Lep2Pt', 'Jet1Pt', 'Jet2Pt','nLep_signal', 'nJet25', 'mll', 'ptll', 'dphi_l1met', 'dphi_l2met', 'dphi_j1met', 'dphi_j2met', 'dphi_l1l2', 'lep_charge', 'qlql','METoverHt', 'Ht30', 'lep_type', 'Mt', 'Mt_l1met','Mt_l2met', 'MTauTau', 'muPt', 'elPt', 'nVtx', 'mu' ]
    variables7 = ['MET', 'Lep1Pt', 'Lep1Eta', 'Lep2Pt', 'Lep2Eta', 'Jet1Pt', 'Jet2Pt','nLep_signal', 'nJet25', 'mll', 'ptll', 'dphi_l1met', 'qlql','METoverHt', 'Ht30', 'lep_type', 'MTauTau', 'muPt', 'elPt' ]
    variables1 = ['mu']
    variables2 = ['mll']

    if args.vars == '0': var_list = variables
    elif args.vars == '1': var_list = variables1
    elif args.vars == '2': var_list = variables2
    elif args.vars == '4': var_list = variables4
    elif args.vars == '5': var_list = variables5
    elif args.vars == '6': var_list = variables6
    elif args.vars == '7': var_list = variables7

    #var_list = variables
    for v in var_list:
        print v
        skim_path = 'presel/presel_skim/h_presel_skim_%s' % v
        dimuon_path = 'select/select_dimuon/h_select_dimuon_%s' % v
        if args.test: print "running plot()"
        print args.indir
        plot(skim_path, 'skim', v,  args.indir, args.test)
        plot(dimuon_path, 'dimuon', v,  args.indir, args.test)
    #GetRootHists(GetRootFiles(args.indir, 0), sample_path, args.test)
    #files = GetRootFiles(args.indir, 0)
    #print files
    #for f in files:
    #    print 'is background? %s' % IsBkgnd(f)
    #    print 'is data? %s' % IsData(f)

    #SumMCHists(GetMCHists(GetRootFiles(args.indir, 0), sample_path, args.test)).Draw()
    #plot(ttbar_path, 'ttbar',  args.indir, args.test)
    #plot(wjets_path, 'wjets', args.indir, args.test)


    if args.test:
        print "Done"



if __name__ == '__main__':
    main(sys.argv[1:])
 #======================================================================
