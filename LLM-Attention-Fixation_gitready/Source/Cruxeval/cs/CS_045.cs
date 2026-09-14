using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, string letter) {
        var counts = new Dictionary<char, int>();
        foreach(var charr in text)
        {
            if (!counts.ContainsKey(charr))
            {
                counts[charr] = 1;
            }
            else
            {
                counts[charr] += 1;
            }
        }
        if(counts.ContainsKey(letter[0]))
            return counts[letter[0]];
        else
            return 0;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("za1fd1as8f7afasdfam97adfa"), ("7")) == (2L));
    }

}
