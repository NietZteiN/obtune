using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(string text) {
        var d = new Dictionary<char, long>();
        foreach (var charr in text.Replace("-", "").ToLower())
        {
            if (d.ContainsKey(charr))
            {
                d[charr]++;
            }
            else
            {
                d[charr] = 1;
            }
        }
        var sortedDict = d.OrderBy(x => x.Value).ToList();
        return sortedDict.Select(x => x.Value).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("x--y-z-5-C")).SequenceEqual((new List<long>(new long[]{(long)1L, (long)1L, (long)1L, (long)1L, (long)1L}))));
    }

}
