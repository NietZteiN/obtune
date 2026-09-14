using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string new_value, long index) {
        var key = text.ToCharArray();
        key[index] = new_value[0];
        return new string(key);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("spain"), ("b"), (4L)).Equals(("spaib")));
    }

}
