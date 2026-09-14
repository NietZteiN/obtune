using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        var textList = text.Split(',').ToList();
        textList.RemoveAt(0);
        int indexT = textList.IndexOf("T");
        textList.Insert(0, textList[indexT]);
        textList.RemoveAt(indexT + 1);
        return "T," + String.Join(",", textList);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Dmreh,Sspp,T,G ,.tB,Vxk,Cct")).Equals(("T,T,Sspp,G ,.tB,Vxk,Cct")));
    }

}
