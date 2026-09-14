using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(List<long> ints) {
        var counts = new int[301];

        foreach (var i in ints)
        {
            counts[i]++;
        }

        var r = new List<string>();
        for (int i = 0; i < counts.Length; i++)
        {
            if (counts[i] >= 3)
            {
                r.Add(i.ToString());
            }
        }
        Array.Clear(counts, 0, counts.Length);
        return string.Join(" ", r);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)2L, (long)3L, (long)5L, (long)2L, (long)4L, (long)5L, (long)2L, (long)89L}))).Equals(("2")));
    }

}
