using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string chars) {
        int num_applies = 2;
        string extra_chars = "";
        for (int i = 0; i < num_applies; i++)
        {
            extra_chars += chars;
            text = text.Replace(extra_chars, "");
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("zbzquiuqnmfkx"), ("mk")).Equals(("zbzquiuqnmfkx")));
    }

}
