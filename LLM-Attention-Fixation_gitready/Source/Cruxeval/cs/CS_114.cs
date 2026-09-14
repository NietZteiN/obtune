using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<string> F(string text, string sep) {
        return text.Split(new[] { sep }, StringSplitOptions.None).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("a-.-.b"), ("-.")).SequenceEqual((new List<string>(new string[]{(string)"a", (string)"", (string)"b"}))));
    }

}
