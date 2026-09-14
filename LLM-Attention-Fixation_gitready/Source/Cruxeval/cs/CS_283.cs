using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(Dictionary<string,long> dictionary, string key) {
        dictionary.Remove(key);
        if (dictionary.Min(kvp => kvp.Key) == key) {
            key = dictionary.Keys.First();
        }
        return key;
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"Iron Man", 4L}, {"Captain America", 3L}, {"Black Panther", 0L}, {"Thor", 1L}, {"Ant-Man", 6L}}), ("Iron Man")).Equals(("Iron Man")));
    }

}
