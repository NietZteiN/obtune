using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string changes) {
        string result = "";
        int count = 0;
        char[] changesArray = changes.ToCharArray();
        foreach (char c in text) {
            if (c == 'e') {
                result += c;
            } else {
                result += changesArray[count % changesArray.Length];
            }
            count += (c != 'e' ? 1 : 0);
        }
        return result;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("fssnvd"), ("yes")).Equals(("yesyes")));
    }

}
