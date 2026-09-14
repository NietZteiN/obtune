using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string prefix) {
        int prefixLength = prefix.Length;
        if (text.StartsWith(prefix))
        {
            return new string(text.Skip((prefixLength - 1) / 2)
                                  .Take((prefixLength + 1) / 2 * -1)
                                  .Reverse()
                                  .ToArray());
        }
        else
        {
            return text;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("happy"), ("ha")).Equals(("")));
    }

}
