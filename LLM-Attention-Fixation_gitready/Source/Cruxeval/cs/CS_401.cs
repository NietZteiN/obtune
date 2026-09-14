using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string suffix) {
        if (!string.IsNullOrEmpty(suffix) && text.EndsWith(suffix))
        {
            return text.Substring(0, text.Length - suffix.Length);
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("mathematics"), ("example")).Equals(("mathematics")));
    }

}
