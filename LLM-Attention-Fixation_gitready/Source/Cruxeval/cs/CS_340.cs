using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        int uppercaseIndex = text.IndexOf('A');
        if (uppercaseIndex >= 0) {
            return text.Substring(0, uppercaseIndex) + text.Substring(text.IndexOf('a') + 1);
        }
        else {
            char[] sortedChars = text.ToCharArray();
            Array.Sort(sortedChars);
            return new string(sortedChars);
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("E jIkx HtDpV G")).Equals(("   DEGHIVjkptx")));
    }

}
