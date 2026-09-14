using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(List<long> plot, long delin) {
        if (plot.Contains(delin))
        {
            int split = plot.IndexOf(delin);
            List<long> first = plot.GetRange(0, split);
            List<long> second = plot.GetRange(split + 1, plot.Count - split - 1);
            return first.Concat(second).ToList();
        }
        else
        {
            return plot;
        }
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)2L, (long)3L, (long)4L})), (3L)).SequenceEqual((new List<long>(new long[]{(long)1L, (long)2L, (long)4L}))));
    }

}
