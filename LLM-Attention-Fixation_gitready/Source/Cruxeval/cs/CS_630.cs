using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;

class Problem {
    public static bool Equals<TKey, TValue>(Dictionary<TKey, TValue> dict1, Dictionary<TKey, TValue> dict2)
    {
        var dict3 = dict2.Where(x => !dict1.ContainsKey(x.Key) || !EqualityComparer<TValue>.Default.Equals(dict1[x.Key], x.Value))
                         .Union(dict1.Where(x => !dict2.ContainsKey(x.Key) || !EqualityComparer<TValue>.Default.Equals(dict2[x.Key], x.Value)))
                         .ToDictionary(x => x.Key, x => x.Value);
        return dict3.Count == 0;
    }

    public static Dictionary<long, long> F(Dictionary<long, long> original, Dictionary<long, long> str) {
        var temp = new Dictionary<long, long>(original);
        foreach (var kvp in str)
        {
            temp[kvp.Value] = kvp.Key;
        }
        return temp;
    }
    public static void Main(string[] args) {
    Debug.Assert(Equals(F((new Dictionary<long,long>(){{1L, -9L}, {0L, -7L}}), (new Dictionary<long,long>(){{1L, 2L}, {0L, 3L}})), (new Dictionary<long,long>(){{1L, -9L}, {0L, -7L}, {2L, 1L}, {3L, 0L}})));
    }

}
