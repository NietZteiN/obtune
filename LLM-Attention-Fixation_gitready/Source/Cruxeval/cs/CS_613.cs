using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text) {
        string result = "";
        int mid = (text.Length - 1) / 2;
        for (int i = 0; i < mid; i++)
        {
            result += text[i];
        }
        for (int i = mid; i < text.Length - 1; i++)
        {
            result += text[mid + text.Length - 1 - i];
        }
        return result.PadRight(text.Length, text[text.Length - 1]);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("eat!")).Equals(("e!t!")));
    }

}
