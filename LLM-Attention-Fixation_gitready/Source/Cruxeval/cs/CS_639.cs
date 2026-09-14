using System;
using System.Numerics;
using System.Diagnostics;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Security.Cryptography;
class Problem {
    public static string F(string perc, string full) {
        string reply = "";
        int i = 0;
        while (perc[i] == full[i] && i < full.Length && i < perc.Length) {
            if (perc[i] == full[i]) {
                reply += "yes ";
            } else {
                reply += "no ";
            }
            i++;
        }
        return reply;
    }
    public static void Main(string[] args) {
    Debug.Assert(F(("xabxfiwoexahxaxbxs"), ("xbabcabccb")).Equals(("yes ")));
    }

}
