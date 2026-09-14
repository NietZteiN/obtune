using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<Tuple<long, long>> F(Dictionary<long,long> d) {
        List<Tuple<long, long>> sorted_pairs = d.OrderBy(x => (x.Key + x.Value).ToString().Length).Select(p => Tuple.Create(p.Key, p.Value)).ToList();
        return sorted_pairs.Where(t => t.Item1 < t.Item2).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<long,long>(){{55L, 4L}, {4L, 555L}, {1L, 3L}, {99L, 21L}, {499L, 4L}, {71L, 7L}, {12L, 6L}})).SequenceEqual((new List<Tuple<long, long>>(new Tuple<long, long>[]{(Tuple<long, long>)Tuple.Create(1L, 3L), (Tuple<long, long>)Tuple.Create(4L, 555L)}))));
    }

}
