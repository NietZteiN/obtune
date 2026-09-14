using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static List<long> F(Dictionary<long,long> d) {
        List<long[]> result = Enumerable.Repeat<long[]>(null, d.Count).ToList();
        int a = 0, b = 0;
        while (d.Count > 0) {
            KeyValuePair<long, long> item;
            if (a == b) {
                item = d.First();
                d.Remove(item.Key);
            } else {
                item = d.Last();
                d.Remove(item.Key);
            }
            result[a] = new long[] { item.Key, item.Value };
            a = b;
            b = (b + 1) % result.Count;
        }
        return result.SelectMany(i => i.ToList()).ToList();
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<long,long>())).SequenceEqual((new List<long>())));
    }

}
