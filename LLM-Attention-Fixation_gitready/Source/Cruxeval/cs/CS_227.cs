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
        char head = text[0];
        string tail = text.Substring(1);
        return char.ToUpper(head) + tail;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Manolo")).Equals(("Manolo")));
    }

}
