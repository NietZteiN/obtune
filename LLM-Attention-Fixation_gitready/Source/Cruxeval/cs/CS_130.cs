using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(Dictionary<string,long> m) {
        var items = m.ToList();
        for(var i = items.Count - 2; i >= 0; i--)
        {
            var tmp = items[i];
            items[i] = items[i+1];
            items[i+1] = tmp;
        }
        var keys = m.Keys.ToArray();
        return string.Format(((m.Count % 2 == 0) ? "{0}={1}" : "{1}={0}"), keys[0], keys[1]);
    }
    public static void Main(string[] args) {
    Debug.Assert(F((new Dictionary<string,long>(){{"l", 4L}, {"h", 6L}, {"o", 9L}})).Equals(("h=l")));
    }

}
