using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long num) {
        int req = (int)num - text.Length;
        text = text.PadLeft((int)(num - req) / 2 + text.Length, '*').PadRight((int)num, '*');
        return text.Substring(req / 2, text.Length - req);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a"), (19L)).Equals(("*")));
    }

}
