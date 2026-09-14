using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long length) {
        length = length < 0 ? -length : length;
        string output = "";
        for (int idx = 0; idx < length; idx++) {
            if (text[idx % text.Length] != ' ') {
                output += text[idx % text.Length];
            }
            else {
                break;
            }
        }
        return output;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("I got 1 and 0."), (5L)).Equals(("I")));
    }

}
