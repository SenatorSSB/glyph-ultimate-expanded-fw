/* Test-only appended observer; the pinned CDC/FIFO implementation is unchanged. */
void fixture_cdc_init(void) {
 cdcd_init();
 _cdcd_itf[0].ep_in=0x81; _cdcd_itf[0].ep_out=0x02;
 _cdcd_itf[0].line_state=1;
 tu_fifo_set_overwritable(&_cdcd_itf[0].tx_ff,false);
 _prep_out_transaction(&_cdcd_itf[0]);
}
unsigned fixture_rx_pending(void) { return tu_fifo_count(&_cdcd_itf[0].rx_ff); }
