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

    public static Dictionary<long, long> F(Dictionary<long, long> d) {
        var sortedKeys = d.Keys.OrderByDescending(k => k).ToList();
        long key1 = sortedKeys[0];
        long val1 = d[key1];
        d.Remove(key1);

        sortedKeys = d.Keys.OrderByDescending(k => k).ToList();
        long key2 = sortedKeys[0];
        long val2 = d[key2];
        d.Remove(key2);

        return new Dictionary<long, long> { { key1, val1 }, { key2, val2 } };
    }
    public static void Main(string[] args) {
    Debug.Assert(Equals(F((new Dictionary<long,long>(){{2L, 3L}, {17L, 3L}, {16L, 6L}, {18L, 6L}, {87L, 7L}})), (new Dictionary<long,long>(){{87L, 7L}, {18L, 6L}})));
    }

}
