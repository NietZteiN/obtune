using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string t = text;
        foreach (char i in text)
        {
            text = text.Replace(i.ToString(), "");
        }
        return text.Length.ToString() + t;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ThisIsSoAtrocious")).Equals(("0ThisIsSoAtrocious")));
    }

}
