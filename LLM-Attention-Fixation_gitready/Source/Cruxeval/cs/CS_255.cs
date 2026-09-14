using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string fill, long size) {
        if (size < 0) {
            size = -size;
        }
        if (text.Length > size) {
            return text.Substring(text.Length - (int)size);
        }
        return text.PadLeft((int)size, fill[0]);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("no asw"), ("j"), (1L)).Equals(("w")));
    }

}
