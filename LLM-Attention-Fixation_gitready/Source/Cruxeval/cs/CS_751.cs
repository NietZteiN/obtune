using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, string charStr, long min_count) {
        var count = text.Count(x => x == charStr[0]);
        if (count < min_count)
        {
            return new string(text.Select(c => char.IsUpper(c) ? char.ToLower(c) : char.ToUpper(c)).ToArray());
        }
        return text;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("wwwwhhhtttpp"), ("w"), (3L)).Equals(("wwwwhhhtttpp")));
    }

}
