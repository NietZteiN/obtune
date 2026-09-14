using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string chars) {
        string s = "";
        foreach(char ch in chars)
        {
            if (chars.Count(c => c == ch) % 2 == 0)
            {
                s += char.ToUpper(ch);
            }
            else
            {
                s += ch;
            }
        }
        return s;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("acbced")).Equals(("aCbCed")));
    }

}
