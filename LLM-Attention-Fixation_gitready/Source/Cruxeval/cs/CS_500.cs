using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, string delim) {
        var reversedText = new string(text.Reverse().ToArray());
        return text.Substring(0, reversedText.IndexOf(delim)).Reverse().Aggregate("", (acc, c) => acc + c);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("dsj osq wi w"), (" ")).Equals(("d")));
    }

}
