using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string delimiter) {
        int index = text.LastIndexOf(delimiter);
        if (index == -1) return text;
        return text.Substring(0, index) + text.Substring(index + delimiter.Length);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("xxjarczx"), ("x")).Equals(("xxjarcz")));
    }

}
