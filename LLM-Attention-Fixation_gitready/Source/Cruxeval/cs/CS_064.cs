using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string text, long size) {
        int counter = text.Length;
        for (int i = 0; i < size - (int)(size % 2); i++) {
            text = ' ' + text + ' ';
            counter += 2;
            if (counter >= size) {
                return text;
            }
        }
        return text; // Add this line to cover case where size is smaller than the loop condition
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("7"), (10L)).Equals(("     7     ")));
    }

}
