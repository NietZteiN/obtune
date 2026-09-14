using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(long start, long end, long interval) {
        List<long> steps = new List<long>();
        for (long i = start; i <= end; i += interval)
        {
            steps.Add(i);
        }

        if (steps.Contains(1))
        {
            steps[steps.Count - 1] = end + 1;
        }

        return steps.Count;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((3L), (10L), (1L)) == (8L));
    }

}
