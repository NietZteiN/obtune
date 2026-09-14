using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<Tuple<long, long>> F(List<long> nums) {
        List<Tuple<long, long>> output = new List<Tuple<long, long>>();
        foreach (var n in nums)
        {
            output.Add(new Tuple<long, long>(nums.Count(x => x == n), n));
        }
        output.Sort((x, y) => y.Item1.CompareTo(x.Item1));
        return output;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new List<long>(new long[]{(long)1L, (long)1L, (long)3L, (long)1L, (long)3L, (long)1L}))).SequenceEqual((new List<Tuple<long, long>>(new Tuple<long, long>[]{(Tuple<long, long>)Tuple.Create(4L, 1L), (Tuple<long, long>)Tuple.Create(4L, 1L), (Tuple<long, long>)Tuple.Create(4L, 1L), (Tuple<long, long>)Tuple.Create(4L, 1L), (Tuple<long, long>)Tuple.Create(2L, 3L), (Tuple<long, long>)Tuple.Create(2L, 3L)}))));
    }

}
