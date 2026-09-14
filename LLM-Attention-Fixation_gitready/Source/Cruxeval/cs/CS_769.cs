using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        char[] textList = text.ToCharArray();
        for (int i = 0; i < textList.Length; i++)
        {
            textList[i] = char.IsUpper(textList[i]) ? char.ToLower(textList[i]) : char.ToUpper(textList[i]);
        }
        return new string(textList);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("akA?riu")).Equals(("AKa?RIU")));
    }

}
