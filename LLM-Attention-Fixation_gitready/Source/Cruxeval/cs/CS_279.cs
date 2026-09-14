using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string ans = "";
        while (text != "")
        {
            string x, sep, remainingText;
            x = text.Substring(0, text.IndexOf("("));
            sep = "(";
            remainingText = text.Substring(text.IndexOf("(") + 1);
            ans = x + sep.Replace("(", "|") + ans;
            ans = ans + remainingText[0] + ans;
            text = remainingText.Substring(1);
        }
        return ans;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("")).Equals(("")));
    }

}
