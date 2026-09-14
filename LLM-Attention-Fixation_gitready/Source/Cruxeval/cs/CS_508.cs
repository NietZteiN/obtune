using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string sep, long maxsplit) {
        var splitted = text.Split(new string[] { sep }, StringSplitOptions.None);
        var length = splitted.Length;
        var new_splitted = new List<string>(splitted.Take(length / 2).Reverse());
        new_splitted.AddRange(splitted.Skip(length / 2));
        return string.Join(sep, new_splitted);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ertubwi"), ("p"), (5L)).Equals(("ertubwi")));
    }

}
