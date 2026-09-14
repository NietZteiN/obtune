using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static string F(string text, long limit, string character) {
        if (limit < text.Length) {
            return text.Substring(0, (int)limit);
        }
        return text.PadRight((int)limit, character[0]);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("tqzym"), (5L), ("c")).Equals(("tqzym")));
    }

}
