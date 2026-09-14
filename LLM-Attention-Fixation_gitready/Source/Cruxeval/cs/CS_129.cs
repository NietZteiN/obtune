using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(string text, string search_string) {
        var indexes = new List<long>();
        while (text.Contains(search_string))
        {
            indexes.Add(text.LastIndexOf(search_string));
            text = text.Substring(0, text.LastIndexOf(search_string));
        }
        return indexes;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("ONBPICJOHRHDJOSNCPNJ9ONTHBQCJ"), ("J")).SequenceEqual((new List<long>(new long[]{(long)28L, (long)19L, (long)12L, (long)6L}))));
    }

}
