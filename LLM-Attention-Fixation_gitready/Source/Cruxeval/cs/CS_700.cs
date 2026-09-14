using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static long F(string text) {
        return text.Length - text.Split(new[] {"bot"}, StringSplitOptions.None).Length + 1;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("Where is the bot in this world?")) == (30L));
    }

}
