using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        text = text.ToLower();
        string capitalize = char.ToUpper(text[0]) + text.Substring(1);
        return text[0].ToString() + capitalize.Substring(1);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("this And cPanel")).Equals(("this and cpanel")));
    }

}
