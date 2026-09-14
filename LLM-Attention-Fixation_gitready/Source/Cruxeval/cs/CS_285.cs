using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text, string ch) {
        return text.Count(c => c.ToString() == ch);
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("This be Pirate's Speak for 'help'!"), (" ")) == (5L));
    }

}
