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

    public static Dictionary<string, string> F(Dictionary<string, string> zoo) {
        return zoo.ToDictionary(kv => kv.Value, kv => kv.Key);
    }
    public static void Main(string[] args) {
    Debug.Assert(Equals(F((new Dictionary<string,string>(){{"AAA", "fr"}})), (new Dictionary<string,string>(){{"fr", "AAA"}})));
    }

}
