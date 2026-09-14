using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Numerics;
using System.Security.Cryptography;
using System.Text;
class Problem {
    public static long F(string text, string character) {
        int position = text.Length;
        if (text.Contains(character)) {
            position = text.IndexOf(character);
            if (position > 1) {
                position = (position + 1) % text.Length;
            }
        }
        return position;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("wduhzxlfk"), ("w")) == (0L));
    }

}
