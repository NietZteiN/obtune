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

    public static Dictionary<string, string> F(Tuple<string, string, string> fields, Dictionary<string, string> update_dict) {
        var di = new Dictionary<string, string>();
        di[fields.Item1] = "";
        di[fields.Item2] = "";
        di[fields.Item3] = "";
        
        foreach (var kvp in update_dict)
        {
            di[kvp.Key] = kvp.Value;
        }
        return di;
    }
    public static void Main(string[] args) {
    Debug.Assert(Equals(F((Tuple.Create("ct", "c", "ca")), (new Dictionary<string,string>(){{"ca", "cx"}})), (new Dictionary<string,string>(){{"ct", ""}, {"c", ""}, {"ca", "cx"}})));
    }

}
